interface Props {
  message: string;
}

export function ErrorAlert({ message }: Props) {
  return (
    <div className="error-alert" role="alert">
      <strong>Error</strong>
      <p>{message}</p>
    </div>
  );
}
